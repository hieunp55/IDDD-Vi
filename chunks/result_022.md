![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000466_0852593b00852e5adb26dbeb3d4428f00137cc7fdb1062e98f1edcad5301b874.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000467_19f77fb8d13fa4de282d7533bbfb6cf792ce64305770ea1efde18c963d212d9d.png)

## Repository hướng lưu trữ (Persistence-Oriented Repositories)

Trong những tình huống mà phong cách collection-oriented (hướng tập hợp) không phát huy tác dụng, bạn sẽ cần sử dụng một Repository (kho lưu trữ đối tượng miền) theo kiểu persistence-oriented (hướng lưu trữ) dựa trên thao tác lưu (`save()`). Trường hợp này xảy ra khi cơ chế lưu trữ bền vững của bạn không tự động phát hiện và theo dõi các thay đổi của đối tượng (dù là ngầm định hay tường minh). Điều này thường thấy khi sử dụng một Data Fabric (4) (lưới dữ liệu trong bộ nhớ), hay một tên gọi khác là NoSQL key-value data store (kho lưu trữ dữ liệu khóa - giá trị NoSQL). Mỗi khi tạo mới một instance (thực thể thể hiện) của Aggregate (cụm tập hợp các thực thể và đối tượng giá trị có cùng ranh giới nhất quán) hoặc chỉnh sửa một instance đã có từ trước, bạn sẽ phải đưa nó vào kho dữ liệu bằng cách sử dụng phương thức `save()` hoặc một phương thức tương tự của Repository.

Còn có một yếu tố cân nhắc khác khi lựa chọn hướng tiếp cận persistence-oriented, ngay cả khi bạn đang sử dụng một ORM (Object-Relational Mapping - công cụ ánh xạ đối tượng - quan hệ) có hỗ trợ phong cách collection-oriented. Điều gì sẽ xảy ra nếu bạn thiết kế các Repository theo hướng collection-oriented rồi sau đó lại quyết định thay thế cơ sở dữ liệu quan hệ bằng một kho lưu trữ key-value? Bạn sẽ gặp phải hiệu ứng gợn sóng (ripple effect) lan rộng khắp Application Layer (tầng ứng dụng), bởi vì tầng này sẽ phải sửa đổi để gọi `save()` ở tất cả những nơi diễn ra việc cập nhật Aggregate. Bạn cũng sẽ muốn loại bỏ các phương thức `add()` và `addAll()` khỏi các Repository của mình, vì chúng không còn phù hợp nữa. Trong những trường hợp mà khả năng thay đổi cơ chế lưu trữ trong tương lai là rất thực tế, tốt nhất bạn nên thiết kế với một interface (giao diện lập trình) linh hoạt hơn ngay từ đầu. Mặt trái là ORM hiện tại có thể khiến bạn bỏ sót những lệnh gọi `save()` cần thiết, điều mà bạn chỉ có thể phát hiện ra sau này khi không còn một Unit of Work (3) (đơn vị công việc theo dõi thay đổi) hỗ trợ phía sau. Ưu điểm là pattern (mẫu thiết kế) Repository sẽ cho phép bạn thay thế hoàn toàn cơ chế lưu trữ bền vững với tác động tiềm tàng ở mức tối thiểu lên ứng dụng của bạn.

## Điểm cốt lõi của Repository hướng lưu trữ

Chúng ta phải gọi lệnh `put()` một cách tường minh cho cả đối tượng mới lẫn đối tượng bị thay đổi vào kho lưu trữ, hành động này sẽ thay thế hoàn toàn bất kỳ giá trị nào đã liên kết trước đó với khóa (key) tương ứng. Việc sử dụng các loại kho dữ liệu này giúp đơn giản hóa đáng kể các thao tác đọc và ghi cơ bản của Aggregate. Vì lý do này, đôi khi chúng còn được gọi là Aggregate Store (kho lưu trữ Aggregate) hoặc Aggregate-Oriented Database (cơ sở dữ liệu hướng Aggregate).

Khi sử dụng một in-memory Data Fabric, chẳng hạn như GemFire hoặc Oracle Coherence, hệ thống lưu trữ thực chất là một triển khai của `Map` trong bộ nhớ mô phỏng lại `java.util.HashMap`, trong đó mỗi phần tử được ánh xạ được coi là một entry (mục nhập). Tương tự, khi sử dụng một kho lưu trữ NoSQL như MongoDB hoặc Riak, việc lưu trữ đối tượng tạo cảm giác giống như một collection (tập hợp), thay vì các bảng, hàng và cột.

3. Bạn có thể tạo các bài kiểm thử cho Application Service (14) (dịch vụ ứng dụng) để kiểm tra việc gọi lưu khi cập nhật khi cần thiết. Một triển khai Repository trong bộ nhớ (xem phần nội dung chính ở phần sau của chương) có thể được thiết kế nhằm kiểm tra tính triệt để của các thao tác lưu.

Các hệ thống này lưu trữ các cặp key-value (khóa - giá trị). Về bản chất, đây là một kho lưu trữ tương tự như `Map`, nhưng sử dụng đĩa cứng thay vì bộ nhớ làm phương tiện lưu trữ chính.

Mặc dù cả hai phong cách cơ chế lưu trữ này đều mô phỏng gần đúng một collection kiểu `Map`, nhưng thật không may, chúng ta buộc phải gọi `put()` một cách tường minh cho cả đối tượng mới lẫn đối tượng bị thay đổi vào kho lưu trữ, qua đó thay thế giá trị đã liên kết trước đó với khóa đã cho. Điều này đúng ngay cả khi một đối tượng bị thay đổi về mặt logic vẫn chính là đối tượng đã được lưu trữ, bởi vì các hệ thống này thường không cung cấp một Unit of Work để theo dõi các thay đổi hoặc hỗ trợ phân định ranh giới transaction (giao dịch) nhằm kiểm soát việc ghi dữ liệu mang tính nguyên tử (atomic write). Thay vào đó, mỗi lệnh `put()` và `putAll()` lại đại diện cho một transaction logic riêng biệt.

Việc sử dụng bất kỳ loại kho dữ liệu nào trong số này đều giúp đơn giản hóa đáng kể các thao tác đọc và ghi cơ bản của Aggregate. Ví dụ, hãy xem xét sự đơn giản khi thêm Product (trong Agile Project Management Context - Ngữ cảnh Quản lý Dự án Agile) này vào một data grid (lưới dữ liệu) Coherence, rồi sau đó đọc lại nó ra:

```java
cache.put(product.productId(), product);

```

```java
// sau đó ...
product = cache.get(productId);

```

Ở đây, instance của `Product` được tự động serialize (tuần tự hóa) vào `Map` bằng cơ chế tuần tự hóa chuẩn của Java. Tuy nhiên, giao diện có vẻ đơn giản này có thể gây hiểu nhầm đôi chút. Nếu muốn các domain (miền nghiệp vụ) đạt hiệu năng thực sự cao, bạn sẽ phải làm nhiều hơn thế. Coherence hỗ trợ tuần tự hóa chuẩn của Java khi không có một bộ cung cấp tuần tự hóa tùy chỉnh (custom serialization provider) nào được đăng ký. Nhìn chung, việc sử dụng cơ chế tuần tự hóa mặc định của Java không phải là lựa chọn tối ưu. Nó đòi hỏi một lượng byte phụ trội đáng kể để biểu diễn mỗi đối tượng, và hiệu năng tương đối kém. 4 Chắc hẳn bạn không muốn đầu tư mua một Data Fabric hiệu năng cao rồi lại tự trói chân mình bằng cách làm giảm số lượng đối tượng có thể lưu cache và hạ thấp thông lượng (throughput) tổng thể chỉ vì cơ chế tuần tự hóa chậm chạp. Vì vậy, hãy luôn nhớ rằng khi sử dụng Data Fabric chẳng hạn, tính chất phân tán sẽ được đưa vào hệ thống của bạn. Điều này thường kéo theo một áp lực thiết kế mới vào việc xây dựng domain model (mô hình miền), cụ thể là yêu cầu về cơ chế tuần tự hóa tùy chỉnh hoặc tối thiểu là chuyên biệt hóa. Điều đó có thể khiến bạn phải đưa ra những quyết định khác biệt, ít nhất là ở cấp độ triển khai.

4. Nó cũng giới hạn các client của Coherence chỉ ở môi trường Java, trong khi các client .NET và C++ cũng có thể sử dụng dữ liệu trên lưới nếu bạn cung cấp cơ chế tuần tự hóa Portable Object Format (POF).

dạng tài liệu (document) của chúng và sau đó chuyển đổi ngược lại về dạng đối tượng. Dĩ nhiên, việc giải quyết các thách thức này không quá khó khăn. Chẳng hạn, việc tạo ra một cơ chế tuần tự hóa tối ưu cho một Aggregate được lưu trữ bởi GemFire hoặc Coherence không hề phức tạp hơn việc tạo các mô tả ánh xạ cho một bộ ORM. Nhưng nó cũng không đơn giản đến mức chỉ việc sử dụng `put()` và `get()` trên một `Map`.

Tiếp theo, tôi sẽ minh họa cách tạo một Repository hướng lưu trữ cho Coherence, và sau đó tôi sẽ nêu bật một số kỹ thuật để thực hiện điều tương tự cho MongoDB.

## Triển khai với Coherence

Tương tự như những gì chúng ta đã làm với Repository hướng tập hợp, trước tiên chúng ta định nghĩa một interface rồi sau đó là phần triển khai (implementation) của nó. Dưới đây là một interface hướng lưu trữ định nghĩa các phương thức dựa trên thao tác `save()` được sử dụng cho data grid Oracle Coherence:

```java
package com.saasovation.agilepm.domain.model.product;

import java.util.Collection;
import com.saasovation.agilepm.domain.model.tenant.Tenant;

public interface ProductRepository {
    public ProductId nextIdentity();
    public Collection<Product> allProductsOfTenant(Tenant aTenant);
    public Product productOfId(Tenant aTenant, ProductId aProductId);
    public void remove(Product aProduct);
    public void removeAll(Collection<Product> aProductCollection);
    public void save(Product aProduct);
    public void saveAll(Collection<Product> aProductCollection);
}

```

`ProductRepository` này không hoàn toàn khác biệt so với `CalendarEntryRepository` ở phần trước. Nó chỉ khác ở cách thức cho phép đưa các instance của Aggregate vào tập hợp được mô phỏng. Trong trường hợp này, chúng ta có các phương thức `save()` và `saveAll()` thay vì các phương thức `add()` và `addAll()`. Cả hai kiểu phương thức về mặt logic đều thực hiện những việc tương tự nhau. Điểm khác biệt chính nằm ở cách mà client sử dụng các phương thức này. Xin nhắc lại, khi sử dụng phong cách collection-oriented, các instance của Aggregate chỉ được thêm vào khi chúng được tạo mới. Còn khi sử dụng phong cách persistence-oriented, các instance của Aggregate phải được lưu lại trong cả hai trường hợp: khi chúng được tạo mới và khi chúng bị sửa đổi:

```java
Product product = new Product(...);
productRepository.save(product);

```

```java
// sau đó ...
Product product = productRepository.productOfId(tenantId, productId);
product.reprioritizeFrom(backlogItemId, orderOfPriority);
productRepository.save(product);

```

Ngoại trừ điểm đó, các chi tiết cụ thể nằm ở phần triển khai. Vì vậy, chúng ta hãy đi sâu ngay vào phần đó. Trước hết, hãy xem xét hạ tầng Coherence mà chúng ta cần để kết nối tới bộ nhớ cache của data grid:

```java
package com.saasovation.agilepm.infrastructure.persistence;

import com.tangosol.net.CacheFactory;
import com.tangosol.net.NamedCache;

public class CoherenceProductRepository implements ProductRepository {
    private Map<Tenant, NamedCache> caches;

    public CoherenceProductRepository() {
        super();
        this.caches = new HashMap<Tenant, NamedCache>();
    }
    ...
    private synchronized NamedCache cache(TenantId aTenantId) {
        NamedCache cache = this.caches.get(aTenantId);

        if (cache == null) {
            cache = CacheFactory.getCache(
                "agilepm.Product." + aTenantId.id(),
                Product.class.getClassLoader());

            this.caches.put(aTenantId, cache);
        }

        return cache;
    }
    ...
}

```

Trong trường hợp của Agile Project Management Context, đội ngũ phát triển đã lựa chọn đặt các triển khai kỹ thuật của Repository tại Infrastructure Layer (tầng hạ tầng).

Cùng với một hàm khởi tạo (constructor) không tham số đơn giản, điểm mấu chốt của Coherence chính là `NamedCache`. Trong số các gói import, hãy lưu ý những lớp đặc thù dùng để tạo hoặc kết nối và sử dụng một cache: `CacheFactory` và `NamedCache`. Cả hai lớp này đều nằm trong package `com.tangosol.net`.

Phương thức `private` `cache()` là phương tiện để lấy được một `NamedCache`. Phương thức này sẽ lấy cache theo cơ chế lazy (nạp lười / trì hoãn nạp) trong lần đầu tiên Repository cố gắng sử dụng nó. Nguyên nhân chủ yếu là vì mỗi cache được đặt tên theo từng Tenant (người thuê / tổ chức thuê bao) cụ thể và Repository phải đợi cho đến khi một phương thức `public` được gọi thì mới có quyền truy cập vào `TenantId`. Có rất nhiều chiến lược đặt tên cho cache trong Coherence có thể được thiết kế. Trong trường hợp này, đội ngũ phát triển đã chọn lưu cache bằng cách sử dụng namespace (không gian tên) sau:

1. Cấp thứ nhất theo tên viết tắt của Bounded Context: `agilepm`
2. Cấp thứ hai theo tên đơn giản của Aggregate: `Product`
3. Cấp thứ ba theo định danh duy nhất của từng tenant: `TenantId`

Cách làm này mang lại một vài lợi ích. Trước hết, mô hình của từng Bounded Context, Aggregate và tenant do Coherence quản lý có thể được tinh chỉnh và mở rộng quy mô một cách riêng biệt. Ngoài ra, mỗi tenant hoàn toàn bị cô lập khỏi tất cả các tenant khác, do đó các truy vấn cho một tenant không thể vô tình lấy nhầm các đối tượng của các tenant khác. Đây cũng chính là động lực tương tự như khi áp dụng kỹ thuật "striping" trên mỗi bảng thực thể với tenant ID trong giải pháp lưu trữ bằng MySQL, nhưng trong trường hợp này nó thậm chí còn sạch sẽ hơn. Hơn nữa, bất cứ khi nào cần một phương thức tìm kiếm (finder method) để trả về toàn bộ các instance của Aggregate cho một tenant nhất định, trên thực tế sẽ không cần phải thực hiện truy vấn nào. Phương thức tìm kiếm chỉ đơn giản yêu cầu Coherence cung cấp toàn bộ các entry trong cache. Bạn sẽ thấy sự tối ưu hóa này ở phần sau thông qua triển khai của `allProductsOfTenant()`.

> 💡 **Giải thích thêm:** "Striping" (phân dải/chia lát dữ liệu) trong bối cảnh cơ sở dữ liệu quan hệ (RDBMS) đa người thuê (multi-tenancy) đề cập đến kỹ thuật thêm một cột phân biệt người thuê (chẳng hạn `tenant_id`) vào tất cả các bảng thực thể. Việc này đảm bảo toàn bộ dữ liệu của các tenant dùng chung bảng nhưng vẫn được lọc tách biệt theo tenant ID trên mỗi truy vấn.
> (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Khi mỗi `NamedCache` được tạo ra hoặc kết nối tới, nó sẽ được đưa vào `Map` liên kết với biến thể hiện `caches`. Điều này cho phép tra cứu nhanh từng cache theo `TenantId` trong tất cả các lần sử dụng tiếp theo sau lần đầu tiên.

Có quá nhiều cân nhắc về cấu hình và tinh chỉnh Coherence để có thể bàn hết ở đây. Bản thân nó là cả một đề tài thảo luận riêng biệt, và các tài liệu chuyên sâu đã đề cập đến điều này. Tôi xin nhường lại chủ đề này cho Aleks Seovi þ [Seovi þ]. Bây giờ chúng ta hãy tiếp tục với phần triển khai:

```java
public class CoherenceProductRepository implements ProductRepository {
    ...
    @Override
    public ProductId nextIdentity() {
        return new ProductId(
            java.util.UUID.randomUUID()
                .toString()
                .toUpperCase());
    }
    ...
}

```

Phương thức `nextIdentity()` của `ProductRepository` được triển khai theo cách tương tự như phương thức của `CalendarEntryRepository`. Nó lấy một UUID và dùng nó để khởi tạo một `ProductId`, sau đó trả về kết quả:

```java
public class CoherenceProductRepository implements ProductRepository {
    ...
    @Override
    public void save(Product aProduct) {
        this.cache(aProduct.tenantId())
            .put(this.idOf(aProduct), aProduct);
    }

    @Override
    public void saveAll(Collection<Product> aProductCollection) {
        if (!aProductCollection.isEmpty()) {
            TenantId tenantId = null;
            Map<String, Product> productsMap =
                new HashMap<String, Product>(aProductCollection.size());

            for (Product product : aProductCollection) {
                if (tenantId == null) {
                    tenantId = product.tenantId();
                }
                productsMap.put(this.idOf(product), product);
            }

            this.cache(tenantId).putAll(productsMap);
        }
    }
    ...
    private String idOf(Product aProduct) {
        return this.idOf(aProduct.productId());
    }

    private String idOf(ProductId aProductId) {
        return aProductId.id();
    }
}

```

Để lưu một instance `Product` mới hoặc đã bị sửa đổi vào data grid, hãy sử dụng `save()`. Phương thức `save()` sử dụng `cache()` để lấy instance `NamedCache` ứng với `TenantId` của `Product`. Sau đó, nó đưa instance `Product` vào `NamedCache`. Lưu ý việc sử dụng phương thức `idOf()`, vốn có hai phiên bản nạp chồng (overload), một cho `Product` và một cho `ProductId`. Trong cả hai trường hợp, các phương thức này đều trả về định dạng `String` của định danh duy nhất của `Product`, tức là `ProductId`. Do đó, phương thức `put()` của `NamedCache` (lớp triển khai `java.util.Map`) sẽ nhận một key dạng chuỗi `String` và instance `Product` làm value (giá trị).

Phương thức `saveAll()` có thể phức tạp hơn đôi chút so với những gì bạn mong đợi. Tại sao không đơn giản là lặp qua `aProductCollection` rồi gọi `save()` cho từng phần tử? Chúng ta hoàn toàn có thể làm như vậy. Tuy nhiên, tùy thuộc vào loại cache Coherence cụ thể đang sử dụng, mỗi lần gọi `put()` đều yêu cầu một network request (yêu cầu mạng). Vì vậy, cách tốt nhất là gom lô (batch) tất cả các instance `Product` cần lưu vào một `HashMap` cục bộ đơn giản rồi gửi chúng đi bằng `putAll()`. Điều này giúp giảm thiểu độ trễ mạng xuống mức thấp nhất có thể bằng cách chỉ sử dụng một request duy nhất, vốn là giải pháp tối ưu nhất.

```java
public class CoherenceProductRepository implements ProductRepository {
    ...
    @Override
    public void remove(Product aProduct) {
        this.cache(aProduct.tenant()).remove(this.idOf(aProduct));
    }

    @Override
    public void removeAll(Collection<Product> aProductCollection) {
        for (Product product : aProductCollection) {
            this.remove(product);
        }
    }
    ...
}

```

Triển khai của `remove()` hoạt động chính xác như kỳ vọng. Tuy nhiên, nếu nhìn vào triển khai của `saveAll()`, thì `removeAll()` có thể mang lại sự ngạc nhiên lớn. Rốt cuộc thì chẳng lẽ không có cách nào để xóa một loạt các entry theo lô hay sao? Câu trả lời là không, interface `java.util.Map` chuẩn không cung cấp điều đó, và do đó Coherence cũng không. Vì vậy, trong trường hợp này chúng ta chỉ đơn thuần lặp qua `aProductCollection` và gọi `remove()` cho từng phần tử. Khi xem xét các hậu quả tiềm ẩn của việc chỉ xóa được một phần của collection do lỗi xảy ra trong Coherence, điều này có vẻ nguy hiểm. Tất nhiên, bạn sẽ phải cân nhắc kỹ các yếu tố tác động khi cung cấp một phương thức `removeAll()`, nhưng hãy nhớ rằng thế mạnh lớn của các Data Fabric như GemFire và Coherence chính là tính dư thừa dữ liệu (redundancy) và tính sẵn sàng cao (high availability).

Cuối cùng, chúng ta đi đến các triển khai phương thức của interface nhằm cung cấp một vài cách để tìm kiếm các instance `Product`:

```java
public class CoherenceProductRepository implements ProductRepository {

```

...

```java
@SuppressWarnings("unchecked")
@Override
public Collection<Product> allProductsOfTenant(Tenant aTenant) {
    Set<Map.Entry<String, Product>> entries = this.cache(aTenant).entrySet();
    Collection<Product> products = new HashSet<Product>(entries.size());

    for (Map.Entry<String, Product> entry : entries) {
        products.add(entry.getValue());
    }

    return products;
}

@Override
public Product productOfId(Tenant aTenant, ProductId aProductId) {
    return (Product) this.cache(aTenant).get(this.idOf(aProductId));
}
...
}

```

Phương thức `productOfId()` chỉ cần thực hiện một thao tác `get()` cơ bản trên `NamedCache`, truyền vào định danh của instance `Product` được yêu cầu.

Phương thức `allProductsOfTenant()` chính là phương thức mà tôi đã đề cập trước đó. Thay vì phải sử dụng quy trình lọc entry phức tạp hơn của Coherence, tất cả những gì nó cần làm chỉ là yêu cầu data grid cung cấp toàn bộ các instance `Product` trong `NamedCache` cụ thể đó. Bởi vì mỗi cache đã được phân tách riêng biệt cho từng tenant, nên mọi instance của Aggregate trong cache đều thỏa mãn điều kiện truy vấn.

Như vậy là chúng ta đã hoàn tất lớp `CoherenceProductRepository`. Phần triển khai này cho thấy cách hiện thực hóa một interface trừu tượng bằng cách sử dụng Coherence như một client để lưu trữ dữ liệu bền vững trên bộ nhớ cache của grid rồi tìm kiếm lại sau đó. Nó không trình bày toàn bộ các khía cạnh liên quan đến việc cấu hình và tinh chỉnh Coherence, hay những gì cần thiết để tạo index (chỉ mục) cho từng cache, hoặc thiết kế một bộ serializer gọn nhẹ, hiệu năng cao cho từng domain object. Đó không phải là trách nhiệm của Repository. Hãy tham khảo [Seovi þ] để nắm bắt chi tiết về các chủ đề đó.

## Triển khai với MongoDB

Tương tự như các triển khai Repository khác, có một số cân nhắc triển khai cơ bản. Triển khai trên MongoDB thực chất khá tương đồng với phiên bản Coherence. Dưới đây là cái nhìn tổng quan cấp cao về những gì chúng ta cần:

1. Một phương tiện để serialize các instance của Aggregate sang định dạng của MongoDB, sau đó deserialize (giải tuần tự hóa) từ định dạng đó và tái lập (reconstitute) lại instance của Aggregate.

MongoDB sử dụng một định dạng JSON đặc biệt gọi là BSON, tức là định dạng JSON nhị phân (binary JSON).

2. Một định danh duy nhất do MongoDB sinh ra và gán cho Aggregate.
3. Một tham chiếu tới node/cluster (cụm máy chủ) MongoDB.
4. Một collection riêng biệt để lưu trữ từng kiểu Aggregate. Tất cả các instance của mỗi kiểu Aggregate phải được lưu trữ dưới dạng một tập hợp các tài liệu đã được tuần tự hóa (các cặp key-value) trong collection riêng của chúng.

Hãy cùng đi từng bước qua quá trình xem xét phần triển khai của Repository. Vì chúng ta sẽ sử dụng lại `ProductRepository`, bạn có thể so sánh triển khai này với phiên bản dành cho Coherence (ở phần trước).

```java
public class MongoProductRepository
    extends MongoRepository<Product>
    implements ProductRepository {

    public MongoProductRepository() {
        super();
        this.serializer(new BSONSerializer<Product>(Product.class));
    }
    ...
}

```

Triển khai này nắm giữ một instance của `BSONSerializer`, lớp này được dùng để tuần tự hóa và giải tuần tự hóa tất cả các instance của `Product` (trên thực tế nó được nắm giữ bởi lớp cha `MongoRepository`). Tôi sẽ không đi quá sâu vào chi tiết của `BSONSerializer`. Đó là một giải pháp tự phát triển (custom-developed) nhằm tạo ra các instance `DBObject` của MongoDB từ các instance `Product` (và bất kỳ kiểu Aggregate nào khác) rồi chuyển đổi ngược lại thành các instance `Product`. Lớp này được cung cấp cùng với các mã nguồn mẫu khác.

Có một vài điểm đáng chú ý mà bạn có thể làm với một `BSONSerializer`. Việc tuần tự hóa và giải tuần tự hóa cơ bản được xử lý bằng cách truy cập trực tiếp vào các trường (field). Điều này giúp giải phóng các domain object của bạn khỏi việc phải triển khai các getter và setter kiểu JavaBean, vốn là thứ dễ kéo bạn đi lệch hướng sang một Anemic Domain Model (mô hình miền thiếu máu - mô hình chỉ chứa dữ liệu mà không có hành vi) [Fowler, Anemic]. Vì bạn sẽ không sử dụng các phương thức để truy cập các trường, nên tại một thời điểm nào đó, bạn sẽ cần phải thực hiện di chuyển dữ liệu (migrate) từ một phiên bản của kiểu Aggregate sang một phiên bản khác. Để làm điều đó, bạn có thể chỉ định các ánh xạ ghi đè (override mapping) cho từng trường trong quá trình giải tuần tự hóa:

```java
public class MongoProductRepository
    extends MongoRepository<Product>
    implements ProductRepository {

```

```java
    public MongoProductRepository() {
        super();
        this.serializer(new BSONSerializer<Product>(Product.class));

        Map<String, String> overrides = new HashMap<String, String>();
        overrides.put("description", "summary");

        this.serializer().registerOverrideMappings(overrides);
    }
    ...
}

```

Trong ví dụ này, chúng ta giả định rằng một phiên bản trước đó của lớp `Product` có một trường mang tên `description`. Ở phiên bản tiếp theo, trường này được đổi tên thành `summary`. Để giải quyết vấn đề này, chúng ta có thể chạy một kịch bản di chuyển dữ liệu (migration script) trên toàn bộ các collection MongoDB dùng để lưu trữ các instance `Product` cho từng tenant. Tuy nhiên, đó có thể là một chuỗi thao tác rất khó khăn và tốn nhiều thời gian, khiến nó trở thành một cách tiếp cận không thực tế. Thay vào đó, chúng ta chỉ cần yêu cầu `BSONSerializer` ánh xạ bất kỳ trường BSON nào trên `Product` có tên là `description` sang trường có tên là `summary`. Sau đó, khi `Product` đã được chuyển đổi này được tuần tự hóa ngược lại thành một `DBObject` và lưu vào collection của MongoDB, bản tuần tự hóa mới sẽ chứa trường mang tên `summary` thay vì `description`. Tất nhiên, điều đó cũng đồng nghĩa với việc bất kỳ instance `Product` nào chưa từng được đọc và lưu ngược trở lại kho dữ liệu thì vẫn sẽ giữ nguyên tên trường `description` cũ đã lỗi thời. Bạn sẽ phải cân nhắc những sự đánh đổi của phương pháp tiếp cận lazy migration (di chuyển dữ liệu lười/khi cần mới làm) này.

Tiếp theo, chúng ta cần một cách để MongoDB tự sinh ra một định danh duy nhất cho từng instance của Aggregate sử dụng:

```java
public class MongoProductRepository
    extends MongoRepository<Product>
    implements ProductRepository {
    ...
    public ProductId nextIdentity() {
        return new ProductId(new ObjectId().toString());
    }
    ...
}

```

Chúng ta vẫn sử dụng phương thức `nextIdentity()`, nhưng trong triển khai này, chúng ta khởi tạo `ProductId` bằng giá trị `String` của một `ObjectId` mới. Lý do chính là vì chúng ta muốn MongoDB sử dụng cùng một định danh duy nhất mà chúng ta đang nắm giữ ngay trong chính instance của Aggregate. Do đó, khi serialize một `Product` (hoặc một kiểu khác trong một triển khai Repository khác), chúng ta có thể yêu cầu `BSONSerializer` ánh xạ định danh đó vào khóa đặc biệt `_id` của MongoDB:

```java
public class BSONSerializer<T> {
    ...
    public DBObject serialize(T anObject) {
        DBObject serialization = this.toDBObject(anObject);
        return serialization;
    }

    public DBObject serialize(String aKey, T anObject) {
        DBObject serialization = this.serialize(anObject);
        serialization.put("_id", new ObjectId(aKey));
        return serialization;
    }
    ...
}

```

Phương thức `serialize()` đầu tiên không hỗ trợ ánh xạ `_id` như vậy, cho phép các client tùy chọn giữ lại các định danh khớp nhau hay không. Tiếp theo, hãy xem cách phương thức `save()` được triển khai:

```java
this.collectionName(aProduct.tenantId()))

```

```java
public class MongoProductRepository
    extends MongoRepository<Product>
    implements ProductRepository {
    ...
    @Override
    public void save(Product aProduct) {
        this.databaseCollection(
            this.databaseName(),
            this.collectionName(aProduct.tenantId()))
            .save(this.serialize(aProduct));
    }
    ...
}

```

Tương tự như triển khai cho Coherence của cùng interface Repository này, chúng ta lấy ra một collection đặc thù cho từng tenant để lưu trữ các instance `Product` ứng với một `TenantId` cho trước. Việc này sẽ trả về một `DBCollection` của Mongo từ một `DB`. Để lấy đối tượng `DBCollection`, chúng ta có đoạn mã sau trong lớp cơ sở trừu tượng `MongoRepository`:

```java
public abstract class MongoRepository<T> {
    ...
    protected DBCollection databaseCollection(
        String aDatabaseName,
        String aCollectionName) {

```

```java
        return MongoDatabaseProvider
            .database(aDatabaseName)
            .getCollection(aCollectionName);
    }
    ...
}

```

Chúng ta sử dụng một `MongoDatabaseProvider` để lấy kết nối tới database instance, kết nối này trả về một đối tượng `DB`. Từ đối tượng `DB` được trả về, chúng ta yêu cầu lấy ra một `DBCollection`. Như đã thấy trong triển khai cụ thể của Repository, collection được đặt tên bằng sự kết hợp giữa chuỗi văn bản "product" và định danh đầy đủ của tenant. Agile PM Context sử dụng một cơ sở dữ liệu chuyên dụng có tên là `agilepm`, rất giống với cách mà triển khai Coherence đặt tên cho bộ nhớ cache của nó:

```java
protected String collectionName(TenantId aTenantId) {

```

```java
public class MongoProductRepository
    extends MongoRepository<Product>
    implements ProductRepository {
    ...
    return "product" + aTenantId.id();
}

protected String databaseName() {
    return "agilepm";
}
...
}

```

Tương tự như `SpringHibernateSessionProvider` đã được giới thiệu trước đó, `MongoDatabaseProvider` là phương tiện để truy xuất một instance của `DB` dùng chung trên toàn bộ ứng dụng.

Cùng một `DBCollection` đó được sử dụng cho cả `save()` lẫn việc tìm kiếm các instance của `Product`:

```java
public class MongoProductRepository
    extends MongoRepository<Product>
    implements ProductRepository {
    ...
    @Override
    public Collection<Product> allProductsOfTenant(
        TenantId aTenantId) {

        Collection<Product> products = new ArrayList<Product>();
        DBCursor cursor = this.databaseCollection(
            this.databaseName(),
            this.collectionName(aTenantId)).find();

```

```java
        while (cursor.hasNext()) {
            DBObject dbObject = cursor.next();
            Product product = this.deserialize(dbObject);
            products.add(product);
        }

        return products;
    }

    @Override
    public Product productOfId(
        TenantId aTenantId,
        ProductId aProductId) {

        Product product = null;
        BasicDBObject query = new BasicDBObject();
        query.put("productId", new BasicDBObject("id", aProductId.id()));

        DBCursor cursor = this.databaseCollection(
            this.databaseName(),
            this.collectionName(aTenantId)).find(query);

        if (cursor.hasNext()) {
            product = this.deserialize(cursor.next());
        }

        return product;
    }
    ...
}

```

Triển khai của `allProductsOfTenant()`, một lần nữa, rất giống với triển khai dành cho Coherence. Chúng ta chỉ đơn giản yêu cầu `DBCollection` theo tenant thực hiện `find()` tất cả các instance. Còn đối với `productOfId()`, lần này chúng ta truyền cho phương thức `find()` của `DBCollection` một `DBObject` mô tả instance `Product` cụ thể cần lấy ra. Trong cả hai phương thức tìm kiếm, chúng ta sử dụng `DBCursor` được trả về để lần lượt lấy ra toàn bộ hoặc chỉ lấy instance đầu tiên.

## Các hành vi bổ sung

Đôi khi, việc cung cấp thêm các hành vi bổ sung trên interface Repository là rất hữu ích, ngoài các hành vi điển hình đã được trình bày ở các phần trước. Một hành vi rất tiện dụng là trả về số lượng đếm của tất cả các instance trong tập hợp Aggregate. Bạn có thể nghĩ đến việc đặt tên cho hành vi này là `count`. Tuy nhiên, vì một Repository nên mô phỏng một collection càng sát càng tốt, bạn có thể cân nhắc sử dụng phương thức sau để thay thế:

```java
public interface CalendarEntryRepository {
    ...
    public int size();
}

```

Phương thức `size()` chính xác là những gì mà một `java.util.Collection` chuẩn mực cung cấp. Khi sử dụng Hibernate, triển khai sẽ hoạt động như sau:

```java
public class HibernateCalendarEntryRepository
    implements CalendarEntryRepository {
    ...
    public int size() {
        Query query = this.session().createQuery(
            "select count(*) from CalendarEntry");

        int size = ((Integer) query.uniqueResult()).intValue();

        return size;
    }
}

```

Có thể có các phép tính toán khác bắt buộc phải thực hiện ngay tại kho dữ liệu (bao gồm cả cơ sở dữ liệu hoặc data grid) nhằm đáp ứng một số yêu cầu phi chức năng nghiêm ngặt. Trường hợp này có thể xảy ra nếu việc di chuyển dữ liệu từ kho lưu trữ đến nơi thực thi business logic (logic nghiệp vụ) quá chậm. Thay vào đó, bạn có thể phải di chuyển mã thực thi đến gần dữ liệu. Điều này có thể được thực hiện bằng cách sử dụng các stored procedure trong cơ sở dữ liệu hoặc các entry processor của data grid, chẳng hạn như những tính năng có sẵn trong Coherence. Tuy nhiên, các triển khai như vậy thường được đặt tối ưu nhất dưới sự kiểm soát của các Domain Service (7) (dịch vụ miền), vì chúng được dùng để chứa các thao tác phi trạng thái (stateless) và mang tính đặc thù của miền.

Đôi khi, việc truy vấn các phần thành phần của Aggregate từ Repository mà không cần truy cập trực tiếp vào chính Root (thực thể gốc) có thể mang lại nhiều lợi thế. Điều này có thể xảy ra nếu một Aggregate nắm giữ một collection lớn gồm một kiểu Entity (thực thể) nào đó, và bạn chỉ cần truy cập vào các instance thỏa mãn một tiêu chí nhất định. Tất nhiên, điều này chỉ hợp lý nếu Aggregate cho phép truy cập như vậy thông qua việc điều hướng từ Root. Bạn sẽ không thiết kế một Repository để cung cấp quyền truy cập vào các phần thành phần mà Aggregate Root bình thường không cho phép truy cập qua đường điều hướng. Làm như vậy sẽ vi phạm giao ước của Aggregate. Tôi cũng khuyên bạn không nên thiết kế Repository cung cấp kiểu truy cập này chỉ như một lối tắt đơn thuần vì sự thuận tiện của client. Tôi cho rằng điều này chỉ nên được sử dụng chủ yếu để giải quyết các mối lo ngại về hiệu năng trong những điều kiện mà việc điều hướng qua Root sẽ gây ra điểm nghẽn cổ chai không thể chấp nhận được. Các phương thức phục vụ việc truy cập tối ưu đó sẽ có các đặc tính cơ bản giống như những phương thức tìm kiếm khác (xem phần trước của chương này), nhưng sẽ trả về các instance của những phần thành phần bên trong thay vì trả về Root Entity. Xin nhắc lại, hãy sử dụng kỹ thuật này một cách thận trọng.

Một lý do khác cũng có thể thôi thúc bạn thiết kế các phương thức tìm kiếm đặc biệt. Một số use case (trường hợp sử dụng) nhất định trong hệ thống của bạn có thể không tuân theo đúng đường ranh giới của một kiểu Aggregate đơn lẻ khi kết xuất view hiển thị dữ liệu miền. Thay vào đó, chúng có thể cắt ngang qua nhiều kiểu, có khả năng chỉ tổng hợp một số phần nhất định của một hoặc nhiều Aggregate. Trong những tình huống như thế này, bạn có thể chọn không thực hiện việc tìm kiếm toàn bộ các instance Aggregate của nhiều kiểu khác nhau trong một transaction đơn lẻ rồi lập trình ghép nối chúng vào một container duy nhất để trả container dữ liệu đó cho client. Thay vào đó, bạn có thể sử dụng giải pháp gọi là use case optimal query (truy vấn tối ưu hóa theo trường hợp sử dụng). Đây là kỹ thuật mà bạn chỉ định một câu truy vấn phức tạp trực tiếp tới cơ chế lưu trữ, rồi nạp động các kết quả vào một Value Object (6) (đối tượng giá trị) được thiết kế chuyên biệt để đáp ứng nhu cầu của use case đó.

Việc một Repository trong một số trường hợp trả về một Value Object thay vì một instance Aggregate là điều không có gì xa lạ. Một Repository cung cấp phương thức `size()` vốn đã trả về một Giá trị rất đơn giản dưới dạng một số nguyên đếm tổng số instance Aggregate mà nó nắm giữ. Một use case optimal query chỉ đơn thuần là mở rộng khái niệm này thêm một chút để cung cấp một Giá trị phức tạp hơn, đáp ứng những yêu cầu phức tạp hơn từ phía client.

Nếu bạn nhận thấy mình phải tạo ra quá nhiều phương thức tìm kiếm hỗ trợ use case optimal query trên nhiều Repository, đó rất có thể là một code smell (dấu hiệu cảnh báo mã nguồn có vấn đề). Trước hết, tình trạng này có thể là dấu hiệu cho thấy bạn đã đánh giá sai ranh giới của Aggregate và bỏ lỡ cơ hội thiết kế một hoặc nhiều Aggregate thuộc các kiểu khác nhau. Code smell ở đây có thể gọi là "Repository che đậy thiết kế sai lầm của Aggregate" (Repository masks Aggregate mis-design).

Tuy nhiên, điều gì sẽ xảy ra nếu bạn gặp phải tình huống này nhưng phân tích của bạn lại chỉ ra rằng các ranh giới Aggregate của bạn đã được thiết kế rất chuẩn mực? Điều này có thể báo hiệu nhu cầu cần xem xét áp dụng CQRS (4) (Command Query Responsibility Segregation - phân tách trách nhiệm giữa lệnh và truy vấn).

## Quản lý Transaction

Mô hình miền và Domain Layer (tầng miền nghiệp vụ) bao quanh nó không bao giờ là nơi phù hợp để quản lý transaction. 5 Các thao tác gắn liền với một model thường quá mịn để có thể tự quản lý transaction và không nên bị phụ thuộc hay nhận thức được rằng transaction đóng một vai trò trong vòng đời của chúng. Nếu phải tránh đưa các mối quan tâm về transaction vào model, thì chúng thực sự thuộc về nơi nào?

5. Lưu ý rằng đối với một số cơ chế lưu trữ bền vững, việc quản lý transaction hoặc là không tồn tại, hoặc hoạt động khác với các transaction tuân thủ thuộc tính ACID (nguyên tử, nhất quán, cô lập, bền vững) phổ biến trong cơ sở dữ liệu quan hệ. Cả Coherence và nhiều kho lưu trữ NoSQL đều có sự khác biệt theo cách đó, và nội dung này nhìn chung không áp dụng cho các cơ chế lưu trữ dữ liệu như vậy.

Một hướng tiếp cận kiến trúc phổ biến để tạo thuận lợi cho việc xử lý transaction thay cho các khía cạnh lưu trữ của domain model là quản lý chúng tại Application Layer (14). 6 Thông thường, chúng ta tạo ra một Facade (mẫu thiết kế mặt tiền) [Gamma et al.] ở tầng đó cho mỗi nhóm use case chính mà ứng dụng/hệ thống cần giải quyết. Facade được thiết kế với các phương thức nghiệp vụ hạt thô, thông thường mỗi phương thức ứng với một luồng use case (có thể chỉ giới hạn ở một phương thức cho một use case nhất định). Mỗi phương thức nghiệp vụ như vậy sẽ điều phối một tác vụ theo yêu cầu của use case. Khi phương thức nghiệp vụ của Facade được gọi bởi User Interface Layer (14) (tầng giao diện người dùng) — dù là đại diện cho con người hay cho một hệ thống khác — phương thức nghiệp vụ đó sẽ khởi đầu một transaction rồi đóng vai trò như một client đối với domain model. Sau khi tất cả các tương tác cần thiết với domain model hoàn tất thành công, phương thức nghiệp vụ của Facade sẽ commit transaction mà nó đã khởi tạo. Nếu xảy ra lỗi/ngoại lệ (exception) ngăn cản việc hoàn thành tác vụ của use case, transaction sẽ được rollback (hoàn tác) bởi chính phương thức nghiệp vụ quản lý đó.

Transaction có thể được quản lý theo kiểu khai báo hoặc theo kiểu tường minh bằng mã lập trình viên viết. Cho dù transaction của bạn là dạng khai báo hay do người dùng tự quản lý bằng mã, những gì tôi mô tả ở đây về mặt logic sẽ hoạt động như sau:

```java
public class SomeApplicationServiceFacade {
    ...
    public void doSomeUseCaseTask() {
        Transaction transaction = null;

        try {
            transaction = this.session().beginTransaction();

            // sử dụng domain model
            ...

            transaction.commit();

        } catch (Exception e) {
            if (transaction != null) {
                transaction.rollback();
            }
        }
    }
}

```

6. Còn có các mối quan tâm khác do Application Layer quản lý, chẳng hạn như bảo mật, nhưng tôi không thảo luận về chúng ở đây.

Để đưa các thay đổi đối với domain model vào trong một transaction, hãy đảm bảo rằng các triển khai Repository có quyền truy cập vào cùng một `Session` hoặc Unit of Work ứng với transaction mà Application Layer đã khởi tạo. Bằng cách đó, các sửa đổi được thực hiện trong Domain Layer sẽ được commit hợp lệ xuống cơ sở dữ liệu bên dưới hoặc được rollback khi có sự cố.

Có vô vàn cách khác nhau để thực hiện điều này đến mức tôi không thể đề cập hết mọi khả năng. Những gì tôi muốn lưu ý là các container Java cho doanh nghiệp và các container Inversion-of-Control (đảo ngược điều khiển - IoC), chẳng hạn như Spring, đều cung cấp phương tiện để thực hiện những gì tôi vừa mô tả, và điều này nhìn chung đã được hiểu rất rõ. Điểm cốt lõi ở đây là hãy sử dụng giải pháp phù hợp với môi trường của bạn. Ví dụ, dưới đây là cách bạn có thể thực hiện bằng Spring:

```xml
<tx:annotation-driven transaction-manager="transactionManager"/>

<bean id="sessionFactory"
      class="org.springframework.orm.hibernate3.LocalSessionFactoryBean">
    <property name="configLocation">
        <value>classpath:hibernate.cfg.xml</value>
    </property>
</bean>

<bean id="sessionProvider"
      class="com.saasovation.identityaccess.infrastructure.persistence.SpringHibernateSessionProvider"
      autowire="byName">
</bean>

<bean id="transactionManager"
      class="org.springframework.orm.hibernate3.HibernateTransactionManager">
    <property name="sessionFactory">
        <ref bean="sessionFactory"/>
    </property>
</bean>

<bean id="abstractTransactionalServiceProxy"
      abstract="true"
      class="org.springframework.transaction.interceptor.TransactionProxyFactoryBean">
    <property name="transactionManager">
        <ref bean="transactionManager"/>
    </property>
    <property name="transactionAttributes">

```

```xml
        <props>
            <prop key="*">PROPAGATION_REQUIRED</prop>
        </props>
    </property>
</bean>

```

Bean `sessionFactory` đã được cấu hình cung cấp phương tiện để lấy một `Session` của Hibernate. Bean có tên `sessionProvider` được sử dụng để liên kết một `Session` nhận được từ `sessionFactory` với `Thread` thực thi hiện tại. Bean `sessionProvider` có thể được các Repository chạy trên nền Hibernate sử dụng khi chúng cần lấy instance `Session` cho `Thread` mà chúng đang chạy bên dưới. `transactionManager` sử dụng `sessionFactory` để nhận và quản lý các transaction Hibernate. Một bean còn lại, `abstractTransactionalServiceProxy`, được sử dụng tùy chọn như một proxy (đối tượng ủy nhiệm) để khai báo các transactional bean bằng cấu hình Spring. Khai báo trên cùng cho phép khai báo các transaction thông qua Java annotation, điều này có thể thuận tiện hơn so với việc sử dụng cấu hình:

<tx:annotation-driven transaction-manager="transactionManager"/>

Khi việc đấu nối này hoàn tất, giờ đây bạn có thể khai báo một phương thức nghiệp vụ nhất định của Facade là có quản lý transaction bằng cách sử dụng một annotation đơn giản:

```java
public class SomeApplicationServiceFacade {
    ...
    @Transactional
    public void doSomeUseCaseTask() {
        // sử dụng domain model
        ...
    }
}

```

So với ví dụ quản lý transaction trước đó, cách này chắc chắn giúp giảm bớt sự rườm rà lộn xộn trong phương thức nghiệp vụ và cho phép bạn tập trung hoàn toàn vào việc điều phối tác vụ. Thông qua annotation này, khi phương thức nghiệp vụ được gọi, Spring sẽ tự động khởi tạo một transaction, và khi phương thức hoàn thành, transaction sẽ được commit hoặc rollback một cách thích hợp.

Dưới đây là mã nguồn của bean `sessionProvider` như được triển khai cho Identity and Access Context:

```java
package com.saasovation.identityaccess.infrastructure.persistence;

import org.hibernate.Session;
import org.hibernate.SessionFactory;

```

## Chương 12: REPOSITORY

```java
public class SpringHibernateSessionProvider {
    private static final ThreadLocal<Session> sessionHolder =
        new ThreadLocal<Session>();

    private SessionFactory sessionFactory;

    public SpringHibernateSessionProvider() {
        super();
    }

    public Session session() {
        Session threadBoundsession = sessionHolder.get();

        if (threadBoundsession == null) {
            threadBoundsession = sessionFactory.openSession();
            sessionHolder.set(threadBoundsession);
        }

        return threadBoundsession;
    }

    public void setSessionFactory(SessionFactory aSessionFactory) {
        this.sessionFactory = aSessionFactory;
    }
}

```

Vì `sessionProvider` là một Spring bean được khai báo với thuộc tính `autowire="byName"`, nên khi bean được khởi tạo dưới dạng singleton (thể hiện duy nhất), phương thức `setSessionFactory()` của nó sẽ được gọi để tiêm (inject) instance của bean `sessionFactory`. Để giúp bạn không phải lật tìm lại phần trước của chương nhằm xem cách một Repository trên nền Hibernate sử dụng bean này như thế nào, dưới đây là một lời nhắc ngắn gọn:

```java
package com.saasovation.identityaccess.infrastructure.persistence;

public class HibernateUserRepository implements UserRepository {
    @Override
    public void add(User aUser) {
        try {
            this.session().saveOrUpdate(aUser);
        } catch (ConstraintViolationException e) {
            throw new IllegalStateException("User is not unique.", e);
        }
    }
    ...
    private SpringHibernateSessionProvider sessionProvider;

    public void setSessionProvider(
        SpringHibernateSessionProvider aSessionProvider) {
        this.sessionProvider = aSessionProvider;
    }

```

```java
    private org.hibernate.Session session() {
        return this.sessionProvider.session();
    }
}

```

Đoạn mã này được trích từ lớp `HibernateUserRepository` của Identity and Access Context. Lớp này cũng là một Spring bean được tự động đấu nối theo tên, nghĩa là phương thức `setSessionProvider()` của nó sẽ tự động được gọi khi tạo để nhận một tham chiếu đến bean `sessionProvider` (một instance của `SpringHibernateSessionProvider`). Khi phương thức `add()` (hoặc bất kỳ phương thức nào khác phục vụ việc lưu trữ bền vững) được gọi, nó sẽ yêu cầu lấy một `Session` thông qua phương thức `session()` của mình. Đến lượt mình, `session()` sẽ sử dụng `sessionProvider` đã được tiêm vào để lấy ra instance `Session` được liên kết với luồng (thread-bound).

Mặc dù tôi mới chỉ minh họa cách quản lý transaction khi sử dụng Hibernate, nhưng tất cả các nguyên tắc này đều có thể áp dụng tương tự cho TopLink, JPA và các cơ chế lưu trữ khác. Với bất kỳ cơ chế lưu trữ nào như vậy, bạn phải tìm cách cung cấp quyền truy cập vào cùng một `Session`, Unit of Work và transaction mà Application Layer đang quản lý. Kỹ thuật Dependency Injection (tiêm phụ thuộc - DI) hoạt động rất tốt cho mục đích này nếu được hỗ trợ. Nếu không có sẵn, vẫn có những cách sáng tạo khác để thiết lập kết nối cần thiết, thậm chí có thể can thiệp đến mức tự liên kết thủ công các đối tượng đó vào thread hiện tại.

## Lời cảnh báo

Tôi thấy có trách nhiệm phải đưa ra một lời cảnh báo sau cùng về việc lạm dụng transaction khi kết hợp với domain model. Các Aggregate phải được thiết kế cẩn trọng nhằm đảm bảo các ranh giới nhất quán (consistency boundary) chính xác. Hãy cẩn thận để không lạm dụng khả năng commit các sửa đổi trên nhiều Aggregate trong một transaction đơn lẻ chỉ vì nó chạy tốt trong môi trường unit test. Nếu không cẩn thận, những gì hoạt động trơn tru trong môi trường phát triển và kiểm thử có thể thất bại nặng nề trên môi trường production (môi trường vận hành thực tế) do các vấn đề tranh chấp đồng thời (concurrency issue). Nếu cần thiết, hãy xem lại chương Aggregates (10) để nắm bắt những lời nhắc quan trọng về việc xác định chính xác ranh giới nhất quán nhằm đảm bảo sự thành công của transaction.

## Cây phân cấp kiểu (Type Hierarchies)

Khi sử dụng một ngôn ngữ hướng đối tượng để phát triển một domain model, việc tận dụng tính kế thừa (inheritance) để tạo ra các cây phân cấp kiểu (type hierarchy) có thể là một cám dỗ khó cưỡng. Chúng ta có thể coi đây là cơ hội để đặt trạng thái và hành vi mặc định vào một lớp cơ sở (base class) rồi sau đó mở rộng bằng các lớp con (subclass). Và tại sao lại không chứ? Nó có vẻ là một cách hoàn hảo để tránh lặp lại chính mình.

Việc tạo ra các Aggregate có chung tổ tiên nhưng lại đứng tách biệt khỏi các họ hàng của chúng bằng một Repository riêng biệt là một cách sử dụng tính kế thừa hoàn toàn khác so với việc tạo ra các Aggregate có cùng tổ tiên nhưng lại dùng chung một Repository duy nhất. Vì vậy, phần này không thảo luận về tình huống mà tất cả các kiểu Aggregate trong một domain model đơn lẻ cùng kế thừa một Layer Supertype (siêu kiểu tầng) [Fowler, P of EAA] để cung cấp trạng thái và/hoặc hành vi chung trên toàn bộ domain. 7

Đúng hơn, ở đây tôi đang đề cập đến việc tạo ra một số lượng tương đối nhỏ các kiểu Aggregate kế thừa từ một siêu lớp (superclass) chung đặc thù của miền. Chúng được thiết kế nhằm tạo thành một cây phân cấp các kiểu có quan hệ mật thiết với nhau, mang các đặc tính đa hình (polymorphic) và có thể thay thế lẫn nhau. Các loại phân cấp này sử dụng một Repository duy nhất để lưu trữ và truy xuất các instance của những kiểu riêng biệt đó, bởi vì client nên sử dụng các instance này thay thế cho nhau được, và client hiếm khi hoặc hầu như không bao giờ phải bận tâm đến lớp con cụ thể nào mà họ đang thao tác tại bất kỳ thời điểm nào — điều này phản ánh Nguyên lý Thay thế Liskov (Liskov Substitution Principle - LSP) [Liskov].

Ý tôi là thế này. Giả sử doanh nghiệp của bạn sử dụng các doanh nghiệp bên ngoài để cung cấp nhiều loại dịch vụ khác nhau, và bạn cần mô hình hóa các mối quan hệ đó. Bạn quyết định xây dựng một lớp cơ sở trừu tượng chung mang tên `ServiceProvider`, nhưng vì một lý do chính đáng nào đó, bạn cần phân tách thành nhiều kiểu cụ thể khác nhau bởi vì các dịch vụ mà mỗi bên cung cấp vừa có điểm chung lại vừa có sự khác biệt rõ rệt. Bạn có thể có một `WarbleServiceProvider` và một `WonkleServiceProvider`. Bạn thiết kế các kiểu này sao cho bạn có thể lên lịch một yêu cầu dịch vụ theo một cách thức chung:

// client của domain model
serviceProviderRepository.providerOf(id)
.scheduleService(date, description);

> 💡 **Giải thích thêm:** "Warble" và "Wonkle" là những định danh giả lập (placeholder/dummy names) do tác giả đặt ra để tượng trưng cho hai loại nhà cung cấp dịch vụ bên ngoài khác nhau về mặt kỹ thuật trong ví dụ minh họa, không phản ánh một công nghệ hay sản phẩm cụ thể nào ngoài đời thực.
> (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Trong bối cảnh này, rõ ràng là việc tạo ra các cây phân cấp kiểu Aggregate đặc thù cho miền có thể sẽ có tính hữu dụng rất hạn chế trong nhiều miền nghiệp vụ. Lý do là vì: Như đã chứng minh trước đó, hầu hết các trường hợp Repository chung sẽ được thiết kế với các phương thức tìm kiếm truy xuất các instance của bất kỳ lớp con nào. Điều đó có nghĩa là phương thức sẽ trả về các instance của siêu lớp chung — trong trường hợp này là `ServiceProvider` — chứ không phải các instance của các lớp con cụ thể như `WarbleServiceProvider` và `WonkleServiceProvider`. Hãy nghĩ xem điều gì sẽ xảy ra nếu các phương thức tìm kiếm được thiết kế để trả về các kiểu cụ thể. Phía client sẽ phải biết được những định danh nào hoặc những thuộc tính mô tả nào của Aggregate sẽ dẫn đến các instance có kiểu cụ thể tương ứng. Nếu không, điều đó có thể dẫn đến việc tìm kiếm không khớp hoặc nảy sinh lỗi `ClassCastException` khi một instance khớp lại trả về sai kiểu mong muốn. Ngay cả khi bạn có thể thiết kế một phương thức tốt để tìm các instance đúng kiểu, client cũng sẽ phải biết lớp con nào có thể thực hiện các thao tác cụ thể khác biệt, xét trong bối cảnh các Aggregate không thể được thiết kế hoàn toàn tuân thủ nguyên lý LSP.

7. Tôi có thảo luận về những lợi ích của việc sử dụng một Layer Supertype trong thiết kế Entities (5) và Value Objects (6). Hãy xem các chương tương ứng.

Để giải quyết vấn đề thứ nhất về việc phân tách các kiểu theo định danh, bạn có thể kết luận rằng mình có thể phát hiện các instance một cách an toàn bằng cách mã hóa thông tin kiểu của Aggregate dưới dạng một trường phân biệt (discriminator) trong lớp của định danh duy nhất. Bạn hoàn toàn có thể làm như vậy. Nhưng điều đó cũng kéo theo hai vấn đề bổ sung. Phía client sẽ phải gánh vác trách nhiệm phân giải và ánh xạ các định danh sang các kiểu tương ứng. Vấn đề mới thứ hai là làm cho client bị gắn kết chặt chẽ (coupling) với các thao tác riêng biệt theo từng kiểu. Nó dẫn đến loại phụ thuộc kiểu ở phía client như thế này:

```java
.scheduleWarbleService(date, warbleDescription);
.scheduleWonkleService(date, wonkleDescription);

```

```java
// client của domain model
if (id.identifiesWarble()) {
    serviceProviderRepository.warbleOf(id)
} else if (id.identifiesWonkle()) {
    serviceProviderRepository.wonkleOf(id)
}
...

```

Nếu kiểu tương tác này trở thành quy chuẩn phổ biến thay vì là trường hợp ngoại lệ, nó báo hiệu một code smell. Đồng ý rằng, nếu những lợi ích thu được từ việc tạo ra cây phân cấp là quá lớn, thì một trường hợp sử dụng cá biệt hiếm hoi như thế này có thể là một sự đánh đổi đáng giá. Tuy nhiên, trong ví dụ giả định này, một thiết kế thấu đáo hơn về kiểu ngầm định `ServiceDescription` cùng triển khai nội bộ của `scheduleService()` có lẽ là đã đủ. Nếu không, tôi nghĩ chúng ta sẽ phải tự hỏi liệu mình có thể thu được lợi ích nào từ việc sử dụng tính kế thừa trong khi vẫn gán cho mỗi kiểu một Repository riêng biệt hay không. Trong trường hợp chỉ cần hai hoặc một vài lớp con cụ thể như vậy, tốt nhất là nên tạo các Repository riêng biệt. Khi số lượng các lớp con cụ thể tăng lên nhiều, và hầu hết chúng đều có thể được sử dụng thay thế hoàn toàn cho nhau (tuân thủ LSP), thì việc để chúng dùng chung một Repository duy nhất mới thực sự đáng giá.

Phần lớn thời gian, loại tình huống này hoàn toàn có thể tránh được bằng cách thiết kế thông tin mô tả kiểu dưới dạng một thuộc tính của Aggregate (chứ không phải trong định danh ID). Hãy xem phần thảo luận về Standard Types (các kiểu chuẩn) trong chương Value Objects (6). Bằng cách này, một kiểu Aggregate đơn lẻ có thể triển khai nội bộ các hành vi khác nhau dựa trên một Standard Type được xác định tường minh. Khi sử dụng một Standard Type tường minh, chúng ta có thể có một Aggregate cụ thể duy nhất là `ServiceProvider` và thiết kế phương thức `scheduleService()` của nó để điều phối (dispatch) hành vi dựa trên kiểu. Để bảo vệ client khỏi các quyết định dựa trên kiểu đó, chúng ta phải đảm bảo rằng logic phân nhánh kiểu không bị rò rỉ ra phía ngoài client. Thay vào đó, `scheduleService()` và các phương thức khác của `ServiceProvider` sẽ đóng gói trọn vẹn những quyết định mang tính đặc thù miền đó, như có thể thấy ở đây:

```java
this.scheduleWarbleService(aDate, aDescription);
this.scheduleWonkleService(aDate, aDescription);
this.scheduleCommonService(aDate, aDescription);

```

```java
public class ServiceProvider {
    private ServiceType type;
    ...
    public void scheduleService(
        Date aDate,
        ServiceDescription aDescription) {

        if (type.isWarble()) {
        } else if (type.isWonkle()) {
        } else {
        }
    }
    ...
}

```

Nếu việc điều phối nội bộ trở nên rườm rà, chúng ta luôn có thể thiết kế một cây phân cấp nhỏ hơn khác để xử lý vấn đề đó. Trên thực tế, bản thân Standard Type hoàn toàn có thể được thiết kế dưới dạng một mẫu State (trạng thái) [Gamma et al.], giả sử bạn ưa thích cách tiếp cận đó. Khi đó, các kiểu khác nhau sẽ triển khai hành vi chuyên biệt của riêng mình. Điều này, dĩ nhiên, cũng đồng nghĩa với việc chúng ta sẽ có một `ServiceProviderRepository` duy nhất, đáp ứng được mong muốn lưu trữ các kiểu khác nhau trong cùng một Repository và sử dụng chúng với hành vi chung.

Tình huống này cũng có thể được giải quyết khéo léo thông qua việc sử dụng các interface dựa trên vai trò (role-based interface). Ở đây, chúng ta có thể quyết định thiết kế một interface `SchedulableService` để nhiều kiểu Aggregate khác nhau cùng triển khai. Hãy xem phần thảo luận về vai trò và trách nhiệm trong chương Entities (5). Ngay cả khi tính kế thừa được sử dụng, hành vi đa hình của Aggregate trong hầu hết các trường hợp đều có thể được thiết kế cẩn trọng sao cho không làm lộ bất kỳ trường hợp ngoại lệ đặc biệt nào ra phía client.

## Phân biệt Repository và Data Access Object

Đôi khi khái niệm Repository bị đánh đồng là đồng nghĩa với Data Access Object (đối tượng truy cập dữ liệu), hay DAO. Đúng là cả hai đều cung cấp một sự trừu tượng hóa trên cơ chế lưu trữ bền vững. Tuy nhiên, một công cụ ánh xạ đối tượng - quan hệ (ORM) cũng cung cấp một sự trừu tượng hóa trên cơ chế lưu trữ bền vững, nhưng nó không phải là Repository cũng chẳng phải là DAO. Vì vậy, chúng ta không thể gọi bừa bất kỳ sự trừu tượng hóa lưu trữ nào là DAO. Thay vào đó, chúng ta phải xác định xem liệu pattern DAO có thực sự đang được triển khai hay không.

Tôi cho rằng nhìn chung có sự khác biệt rõ rệt giữa Repository và DAO. Về cơ bản, một DAO được thể hiện dựa trên các bảng cơ sở dữ liệu và cung cấp các interface CRUD (Create - Read - Update - Delete / Tạo - Đọc - Cập nhật - Xóa) thao tác trên các bảng đó. Martin Fowler trong cuốn [Fowler, P of EAA] đã phân tách việc sử dụng các cơ chế kiểu DAO khỏi những cơ chế được sử dụng cùng với domain model. Ông xác định Table Module (mô-đun bảng), Table Data Gateway (cổng dữ liệu bảng) và Active Record (bản ghi chủ động) là những pattern thường được sử dụng trong một ứng dụng viết theo Transaction Script (kịch bản giao dịch). Đó là bởi vì DAO và các pattern liên quan có xu hướng đóng vai trò như các lớp vỏ bọc (wrapper) bao quanh các bảng cơ sở dữ liệu. Ngược lại, Repository và Data Mapper (bộ ánh xạ dữ liệu), với đặc tính gắn kết chặt chẽ với đối tượng (object affinity), mới là những pattern điển hình được sử dụng với một domain model.